# from dependency_injector import containers, providers

# from server.connection import connect
# from server.request import BaseConnection, Connection



# class MainContainer(containers.DeclarativeContainer):
#     wiring_config = containers.WiringConfiguration(
#         packages=[
#             "server",
#         ]
#     )

#     # core = providers.Container(CoreContainer)

#     # connection: providers.Singleton[BaseConnection] = providers.Singleton(Connection)
#     connection: BaseConnection = providers.Resource(connect)
