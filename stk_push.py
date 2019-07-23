#!/usr/bin/python2.7 -u
from Stk import Stk
from MySQL import MySQL
from stk_configs import logger, config, mysql_params
from functools import partial

import time
import datetime
import logging
import ConfigParser
import os
import signal
import MySQLdb
import MySQLdb.cursors
import sys
import eventlet

eventlet.monkey_patch()

is_sending = 0
is_waiting_to_die = 0

mysql = MySQL()

service_params = None

def signal_handler(signum, frame):
    global is_sending, is_waiting_to_die
    logger.info('SIGNAL:\tSIGTERM')
    if is_sending:
        is_waiting_to_die = 1
        logger.info('SENDING...\t WAIT!')
        return
    logger.info('DIE')
    exit(0)

def init_service_params(service):
    """ Parameters specific to the service
    """
    global service_params
    sections = config.sections()
    try:
        index = sections.index(service)
        name = config.get(sections[index],'name')

        service_params = {'name':name}
    except Exception, e:
        raise

def service_init(args):
    """ Defines how the application is started.
    args = terminal arguments used to run the service """
    app_list = config.sections()
    reserved_sections = ['endpoints', 'mysql', 'logger', 'service']

    #Invalid Arguments or Invalid Params
    if len(args) < 2:
        logger.error("USAGE: python %s <app_name>" % args[0])
        exit(0)
    elif sys.argv[1] not in app_list:
        logger.error('Invalid Args: App %s must be in the config file' % args[1])
        exit(0)
    elif args[1] in reserved_sections:
        logger.error('Invalid Args: %s is a reserved section' % args[1])
        exit(0)
    else:
        try:
            init_service_params(args[1])
            logger.info('%s: %s Started! Name: %s'
                    % (datetime.datetime.now(), args[1], service_params['name']))
        except Exception, e:
            logger.error('Invalid Params in the configuration file. %s' % e)
            exit(0)

def _fetch_from_queue(connection=None):
    """ Retrieve from stk_push transactions
    """

    sql = """SELECT id, session_id, msisdn, amount, transaction_desc, account_no
                FROM stk_push WHERE status = 0  LIMIT 100
          """
    params = ()
    try:
        trx_list = mysql.retrieve_all_data_params(connection, sql, params)
        return trx_list
    except Exception, e:
        logger.error(e)
        raise

def _update_transaction(connection, id, merchant_request_id, check_out_request_id, response_code, response_desc, customer_message):
    del_sql = '''UPDATE stk_push SET status = %s,
                merchant_request_id = %s, checkout_request_id = %s, response_code = %s, response_description = %s, customer_message  = %s 
                WHERE id = %s'''
    params = ('1', merchant_request_id, check_out_request_id, response_code, response_desc, customer_message, id)
    try:
        mysql.execute_query(connection, del_sql, params)
        return True
    except Exception, e:
        logger.error('_update_transaction: %s' % e)
        raise

def _push_to_processed(trx, confirm_resp, checkout_resp, connection):
    insert_sql = """INSERT INTO mpesa_online_deposit
                (msisdn, amount, merchant_trx_id, reference_id, check_out_return_code,
                        check_out_desc, check_out_trx_id, confirm_ret_code, confirm_desc, `timestamp`)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())"""

    params = (trx['MobileNumber'], trx['TransactionAmount'], trx['SessionId'],
        trx['ID'],  checkout_resp['RETURN_CODE'], checkout_resp['DESCRIPTION'], checkout_resp['TRX_ID'],
        confirm_resp['RETURN_CODE'], confirm_resp['DESCRIPTION'])
    try:
        mysql.execute_query(connection, insert_sql, params)
        return True
    except Exception, e:
        logger.error(e)
        raise

def dispatch(connection):
    """ Pops transactions from stk_push
    """
    global is_sending, is_waiting_to_die
    trx_list = _fetch_from_queue(connection)
    try:
        pool_size = 10
        is_sending = True
        pool = eventlet.GreenPool(size=pool_size)
        for response in pool.imap(partial(process_stk, connection), trx_list):
             logger.info('RESP: MerchantRequestID:%s :: CheckoutRequestID:%s :: ResponseCode:%s :: ResponseDescription:%s :: CustomerMessage:%s' %\
                 (response['MerchantRequestID'], response['CheckoutRequestID'], response['ResponseCode'], response['ResponseDescription'], response['CustomerMessage']))
        is_sending = False
        if is_waiting_to_die:
            logger.info('NOT SENDING:\tDIE.')
            exit(0)
    except Exception, e:
        logger.error(e)
        is_sending = 0
        if is_waiting_to_die:
            logger.info('NOT SENDING:\tDIE.')
            exit(0)


def process_stk(connection, trx):
    #time.sleep(5)

    if not len(trx):
        return [{'MerchantRequestID':None, 'CheckoutRequestID':None, 'ResponseCode':None, 'ResponseDescription':None,  'CustomerMessage':None}]
    #connection = None
    print 'calling stk function'
    stk = Stk()
    print 'after calling stk function'
    try:
        #session_id, msisdn, amount, transaction_desc, account_no
        logger.info('REQ: SESSION ID:%s::MSISDN:%s::AMOUNT:%s::TRANSCION DESC:%s::ACCOUNT NO:%s'\
                 %(trx['session_id'], trx['msisdn'], trx['amount'],  trx['transaction_desc'],  trx['account_no']))
        
        desc = trx['transaction_desc']

	response = stk.stk_push(trx['amount'], trx['msisdn'],trx['account_no'] , trx['transaction_desc'])
        logger.info('%s Response'
                    % (response))
        check_out_request_id = response['CheckoutRequestID']
        merchant_request_id = response['MerchantRequestID']
        response_code = response['ResponseCode']
        response_desc = response['ResponseDescription']
        customer_message = response['CustomerMessage']
        

        #logger.info('RESP: MerchantRequestID:%s :: CheckoutRequestID:%s :: ResponseCode:%s :: ResponseDescription:%s :: CustomerMessage:%s' %\
        #         (response['MerchantRequestID'], response['CheckoutRequestID'], response['ResponseCode'], response['ResponseDescription'], response['CustomerMessage']))
        

        _update_transaction(connection, trx['id'], merchant_request_id, check_out_request_id ,response_code, response_desc, customer_message)

        connection.commit()
        return response
    except Exception, e:
        logger.error(e)
        connection.rollback()
    

def create_connection():
    """ Creates a connection and returns the connection """
    try:
        connection = MySQLdb.connect(host=mysql_params['host'],\
                user=mysql_params['user'], passwd=mysql_params['passwd'],\
                db=mysql_params['db'], cursorclass=MySQLdb.cursors.DictCursor)
    except MySQLdb.Error, e:
        logger.error(e)
        raise
    return connection

if __name__=='__main__':
    service_init(sys.argv)
    signal.signal(signal.SIGTERM, signal_handler)
    while True:
        try:
            connection = create_connection()
            dispatch(connection)
        except MySQLdb.Error, e:
            logger.error("MySQL Error: %s" % e)
        finally:
            try:
                connection.close()
            except Exception ,e:
                logger.error("MySQL Error closing connection : %s" % e)
        time.sleep(1)

