## Application space
class ChartService:
  create_subscription_endpoint = Endpoint.CREATE_SUBSCRIPTION_CHART
  
  def __init__(self, registory):
    if registory.find(user_id):
      self.context_id = registory.context_id
      self.subscriptions = registory.subscriptions
      _ = [start_subscription(ref_id, args) for ref_id in self.subscriptions]
      
    else:
      self.context_id = user_id
      self.subscriptions = []
      self.create_connection()

  async def create_connection():
    self.streaming_session = user_session.ws_connect(self.context_id)
    
  async def start_subscription(ref_id, args):
    ref_id = self._new_reference_id()
    try:
      subscription = await self.streaming_session.subscribe(self.create_subscription_endpoint, args) as subscription:
    else:
      self.subscriptions.append(ref_id)
    
    while True:
      msg = subscription
    
