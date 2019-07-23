import logging                                                                                 
import ConfigParser                                                                            
                                                                                               
CONFIG_FILE = r'/usr/local/lib/stk_push/stk.conf'
config = ConfigParser.ConfigParser()                                                           
config.read(CONFIG_FILE)                                                                       


#logging.basicConfig(level=logging.INFO)                                                        
logger = logging.getLogger("MPESA_ONLINE")                                                              
logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)
#hdlr = logging.FileHandler(config.get("logger", "log_file"))                                   
hdlr = logging.StreamHandler()                                   
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')                         
hdlr.setFormatter(formatter)                                                                   
logger.addHandler(hdlr)                                                                        
                                                                                                                                                           
host = config.get("mysql", "host")                                                             
port = config.get("mysql", "port")                                                             
user = config.get("mysql", "user")                                                             
passwd = config.get("mysql", "password")                                                       
db = config.get("mysql", "database")                                                           
connection_timeout = config.get("mysql", "connection_timeout")                                 
mysql_params = {
        'host':host,
        'port':port,
        'user':user,
        'passwd':passwd,
        'db':db,
        'connection_timeout':connection_timeout        
        }

shortcode = config.get("service", "shortcode")                                                       
transaction_type = config.get("service", "transaction_type")                                                                                     
pass_key = config.get("service", "pass_key")                                                  
consumer_key = config.get("service", "consumer_key")
consumer_secret = config.get("service", "consumer_secret") 

service = {                                                                          
    'shortcode':shortcode,
    'transaction_type':transaction_type,                                                                                                                  
    'pass_key':pass_key, 
    'consumer_key':consumer_key,                                                          
    'consumer_secret':consumer_secret
}                                                                                       



result_endpoint = config.get("endpoint", "result_endpoint")                                                       
stkpush_api = config.get("endpoint", "stkpush_api")                                                                                     
stkpushquery_api = config.get("endpoint", "stkpushquery_api")                                                  
authentication = config.get("endpoint", "authentication")                                                                                        

endpoint = {                                                                          
    'result_endpoint':result_endpoint,
    'stkpush_api':stkpush_api,                                                                                                                  
    'stkpushquery_api':stkpushquery_api, 
    'authentication':authentication,                                                          
}                                                                                       
