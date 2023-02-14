from typing import List
from typing import Tuple

from openapi_schema_pydantic import Parameter

from winter.core import ComponentMethodArgument
from winter.web.routing import Route
from winter_openapi.inspection import DataTypes
from winter_openapi.inspection import TypeInfo
from winter_openapi.inspection.inspection import InspectorNotFound
from winter_openapi.inspection.inspection import inspect_type
from winter_openapi.inspectors.route_parameters_inspector import RouteParametersInspector
from winter_openapi.type_info_converter import convert_type_info_to_openapi_schema


class QueryParametersInspector(RouteParametersInspector):

    def inspect_parameters(self, route: 'Route') -> List[Parameter]:
        parameters = []

        for argument, query_parameter_name in self._query_arguments(route):
            openapi_parameter = self._convert_argument_to_openapi_parameter(argument, query_parameter_name)
            parameters.append(openapi_parameter)

        return parameters

    def _convert_argument_to_openapi_parameter(self, argument: ComponentMethodArgument, name: str) -> Parameter:
        try:
            type_info = inspect_type(argument.type_)
            description = argument.description
        except InspectorNotFound:
            type_info = TypeInfo(DataTypes.STRING)
            description = 'winter_openapi has failed to inspect the parameter'
        schema = convert_type_info_to_openapi_schema(type_info, output=False)
        return Parameter(
            name=name,
            description=description,
            required=argument.required,
            param_in='query',
            default=argument.get_default(None),
            param_schema=schema,
        )

    def _query_arguments(self, route: 'Route') -> List[Tuple[ComponentMethodArgument, str]]:
        query_arguments = []
        query_parameters = route.get_query_parameters()

        for query_parameter in query_parameters:
            argument = route.method.get_argument(query_parameter.map_to)
            if argument is not None:
                query_arguments.append((argument, query_parameter.name))
        return query_arguments