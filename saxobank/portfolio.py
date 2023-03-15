# from winko import endpoints
# from winko.interface import PositionSearchQuery

# from saxobank.models.cs.audit import ReqOrderActivities


# async def positions(winko_id: str, search_query: PositionSearchQuery):
#     params = ReqOrderActivities()
#     if search_query.date_from is not None:
#         params.FromDateTime = search_query.date_from

#     if search_query.date_to is not None:
#         params.ToDateTime = search_query.date_to

#     status, res = endpoints.request(endpoints.CS_AUDIT_ORDERACTIVITIES, params)
