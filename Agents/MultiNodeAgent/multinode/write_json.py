import json
multinode_data = {
    'known_nodes':[
         {
            'name':'Node1',
            'address':'tcp://192.168.10.77:9000',
            'server_key':'server1.key',
            'server_secret_key':'server1.key_secret',  #only needed for this_node
            'client_secret_key':'client1.key_secret'    #only needed for this_node
        },
        {
            'name': 'Node2',
            'address': 'tcp://192.168.10.77:9001',
            'server_key': 'server2.key',
            'server_secret_key':'server2.key_secret',   #only needed for this_node
            'client_secret_key':'client2.key_secret'     #only needed for this_node
        },
        {
            'name': 'Node3',
            'address': 'tcp://192.168.10.77:9002',
            'server_key': 'server3.key',
            'server_secret_key':'server3.key_secret',  #only needed for this_node
            'client_secret_key':'client3.key_secret'    #only needed for this_node
        },
        {
            'name': 'Node4',
            'address': 'tcp://192.168.10.77:9003',
            'server_key': 'server4.key',
            'server_secret_key':'server4.key_secret',  #only needed for this_node
            'client_secret_key':'client4.key_secret'    #only needed for this_node
        }
    ],
    'this_node':'Node1'
}


with open('multinode_data.json','w') as f:
    json.dump(multinode_data,f,indent=4)

