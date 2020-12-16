import boto3, os
from datetime import datetime, timedelta, timezone

client = boto3.client('config')

gotten_resources = {}
resources = {}
exception_resources = {}
pre_relation_resources = {}
relationships = []
nest_cnt = 0
nest_max = 3
output_all_relation = False

def nest_mng( func ):
    def inner( type, id ):
        global nest_cnt
        relation_line = "  " * nest_cnt + " +- " + type + " : " + id 
        if id in gotten_resources or nest_cnt > nest_max:
            if output_all_relation:
                relation_line = relation_line + " *"
                relationships.append( relation_line )
            return
        gotten_resources[ id ] = type
        
        try:
            nest_cnt += 1
            ret = func( type, id )

            if ret:
                resources[ id ] = ret
                relationships.append( relation_line )
                
            nest_cnt -= 1
            return ret
        except Exception as e:
            nest_cnt -= 1
            print( "[ERROR]", type, id )
            print( e.args )
            exception_resources[ id ] = e
            return

    return inner


@nest_mng
def dig_relation( type, id ):
    if not id or len( id ) == 0:
        list = client.list_discovered_resources( resourceType=type )
        for r in list['resourceIdentifiers']:
            dig_relation( r['resourceType'], r['resourceId'] )
        return
    
    resource = client.get_resource_config_history(
        resourceType=type,
        resourceId=id,
        limit=1
    )

    enable_resource = False
    for item in resource['configurationItems']:
        if item[ 'configurationItemStatus' ] == 'ResourceDiscovered' or item[ 'configurationItemStatus' ] == 'OK' :
            enable_resource = True
            for rel in item['relationships']:
                t = rel['resourceType']
                i = rel['resourceId']
                dig_relation( t, i )
                
    if not enable_resource:
        return
    
    return resource


if __name__ == '__main__':

    argv = os.sys.argv
    env = os.environ
    JST = timezone(timedelta(hours=+9), 'JST')
    now_str = datetime.now( JST ).strftime("%Y%m%d_%H%M%S")

    if "RELATION_NEST_MAX" in env:
        nest_max = int( env["RELATION_NEST_MAX"] )
        
    if "OUT_ALL_RELATION" in env:
        output_all_relation = True
        
    if len( argv ) == 2:
        dig_relation( argv[1], '' )
        out_file = "resources-" + argv[1] + "_" + now_str + ".json"
    elif len( argv ) == 3:
        dig_relation( argv[1], argv[2]  )
        out_file = "resources-" + argv[1] + "-" + argv[2] + "_" + now_str + ".json"
    else:
        print("[ERROR] Invalid argumments.")
        exit( -1 )

    relationships.reverse()
    for line in relationships:
        print( line )

    if len( resources ) == 0:
        exit( 0 )

    with open( out_file, 'w' ) as out:
        for id in sorted( resources ):
            out.write( "{\n  \"resourceType\":\"" + gotten_resources[id] + "\", \"resourceId\":\"" +  id + "\",\n")
            if id not in exception_resources:
                if resources[ id ][ 'configurationItems' ] is None:
                    print( resources[ id ] )
                else:
                    out.write( "  \"configuration\":" )
                    out.write( resources[ id ][ 'configurationItems' ][0][ 'configuration' ] )
                    out.write( "\n}\n")
            
        print( "\nWrote [", out_file, "]."  )
    
