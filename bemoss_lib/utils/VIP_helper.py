from volttron.platform.vip.agent import Core, Agent
import gevent

def vip_publish(topic,message):
    no_success = True

    while no_success:
        pub_agent = Agent()
        my_event = gevent.event.Event()
        agent_thread = gevent.spawn(pub_agent.core.run, my_event)
        my_event.wait()

        try:
            pub_agent.vip.pubsub.publish(peer='pubsub', topic=topic, message=message).get(timeout=5)
        except gevent.Timeout:
            print "Can't publish. Will try again"
        else:
            no_success = False

        agent_thread.kill()




