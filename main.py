import sys

import os
import oyaml as yaml

swagger_file = 'swagger-config-input/exchange-rates-api-config.yaml'
# http_methods = ['get', 'post', 'put', 'patch', 'delete']
path_method_dictionary = {}


def get_basic_types_example(type, format=None):
    if type == 'string':
        # format is an open value, so you can use any formats in if section, even not defined in OpenAPI Specification
        if format is None:
            return 'Example string'
        elif format == 'date':
            return '2022-07-21'
        elif format == 'date-time':
            return '2017-07-21T17:32:28Z'
        elif format == 'password':
            return '********'
        elif format == 'byte':
            return 'U3dhZ2dlciByb2Nrcw=='
        elif format == 'email':
            return 'test@gmail.com'
        else:
            return 'Example of string with unknown format'
    elif type == 'integer' or (type == 'number' and format == 'integer') \
            or (type == 'number' and format == 'int32') \
            or (type == 'number' and format == 'int64'):
        return 1234
    elif type == 'number':
        if format is None:
            return 1234
        elif format == 'float':
            return 12.34
        elif format == 'double':
            return 12.34
    elif type == 'boolean':
        return True
    elif type == 'array':
        return []
    else:
        return None


def get_example_by_type(type, enum=None, format=None):
    if enum is None:
        return get_basic_types_example(type, format)
    else:
        return enum[0]


def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        swagger_data = yaml.safe_load(file)
        return swagger_data


def write_yaml_file(file_path, swagger_data):
    with open(file_path, 'w') as file:
        yaml.dump(swagger_data, file)


def add_examples_to_config_paths(swagger_data, path_method_dictionary):
    for path, method in path_method_dictionary.items():
        if path in swagger_data['paths'] and method in swagger_data['paths'][path]:
            path_info = swagger_data['paths'][path]
            method_info = path_info[method]

            if 'parameters' not in method_info:
                method_info['parameters'] = []
            else:
                parameters = method_info['parameters']
                for index, key in enumerate(parameters):
                    enum = get_enum(parameters, index)
                    example_format = get_format(parameters, index)
                    example_type = get_example_type(parameters, index)
                    method_info['parameters'][index]['schema']['example'] = get_example_by_type(example_type, enum,
                                                                                                example_format)

    return swagger_data


def add_examples_to_config_dtos(swagger_data):
    dictionary_of_components = get_dictionary_of_components(swagger_data)
    if 'components' in swagger_data:
        if 'schemas' in swagger_data['components']:
            for key, value in dictionary_of_components.items():
                # tuple_of_values = (var_name, var_type, format)
                swagger_data['components']['schemas'][key]['example'] = get_example_obj_by_dto_name(key, dictionary_of_components)

    return swagger_data


def get_example_obj_by_dto_name(dto_name, dictionary_of_components):
    example = {}
    if dto_name in dictionary_of_components:
        list_of_vars = dictionary_of_components[dto_name]
        for elem in list_of_vars:
            if elem[0] in elem:
                # elem = (var_name, var_type, format)
                example[elem[0]] = get_basic_types_example(elem[1], elem[2])
        return example
    else:
        return None


def get_dictionary_of_components(swagger_data):
    # structure of dictionary {dto_name, [(param_name_1, param_type_1, param_format_1), (param_name_2, param_type_2, param_format_2), ...]}
    dictionary_of_components = {}
    list_of_dto_name = get_list_of_dto_name(swagger_data)

    for dto_name in list_of_dto_name:
        dictionary_of_components[dto_name] = get_list_params_tuple_by_dto_name(dto_name, swagger_data)

    return dictionary_of_components


def get_list_of_dto_name(swagger_data):
    if 'components' in swagger_data:
        if 'schemas' in swagger_data['components']:
            return swagger_data['components']['schemas'].keys()


def get_dto_schemas(swagger_data):
    if 'components' in swagger_data:
        if 'schemas' in swagger_data['components']:
            return swagger_data['components']['schemas']


def get_list_params_tuple_by_dto_name(dto_name, swagger_data):
    schemas = get_dto_schemas(swagger_data)
    list_params = []

    if dto_name in schemas:
        if 'properties' in schemas[dto_name]:
            # key = param_name, value = param_object
            for key, value in schemas[dto_name]['properties'].items():
                if 'type' in value and 'format' in value:
                    list_params.append((key, value['type'], value['format']))
                elif 'type' in value and 'format' not in value:
                    list_params.append((key, value['type'], None))
                elif 'format' in value and 'type' not in value:
                    list_params.append((key, value['type'], None))
                else:
                    list_params.append((key, None, None))

    return list_params


def get_enum(parameters, index):
    elem = parameters[index]
    if 'schema' in elem:
        if 'enum' in elem['schema']:
            return elem['schema']['enum']
    return None


def get_example_type(parameters, index):
    elem = parameters[index]
    if 'schema' in elem:
        if 'type' in elem['schema']:
            return elem['schema']['type']
    return None


def get_format(parameters, index):
    elem = parameters[index]
    if 'schema' in elem:
        if 'format' in elem['schema']:
            return elem['schema']['format']
    return None


def file_exists(file_path):
    return os.path.isfile(file_path)


# (1) parse all url path, ad their HTTP methods
# (2) structure of output should be as in input
# TODO: (3) add processing of DTOs
# (4) write global method, that runs add_parameter_to_swagger for every url path
# (5) parameter of filepath should be passed through command line
# TODO: (6) add processing of response schemas
# TODO: (7) test with script on both yaml files
# TODO: (8) push code into the GitHub


def get_path_method_dict(swagger_data):
    for key, value in swagger_data['paths'].items():
        if 'get' in value and type(value['get']) is dict:
            path_method_dictionary[key] = 'get'
        if 'post' in value and type(value['post']) is dict:
            path_method_dictionary[key] = 'post'
        if 'put' in value and type(value['put']) is dict:
            path_method_dictionary[key] = 'put'
        if 'patch' in value and type(value['patch']) is dict:
            path_method_dictionary[key] = 'patch'
        if 'delete' in value and type(value['delete']) is dict:
            path_method_dictionary[key] = 'delete'
    return path_method_dictionary


def main(input_file_path, output_file_path):
    if os.path.isfile(input_file_path):
        print('File exists, the process of adding examples is started')
        # MAIN PROCESSING
        swagger_data = read_yaml_file(input_file_path)

        path_method_dictionary = get_path_method_dict(swagger_data)
        swagger_data = add_examples_to_config_paths(swagger_data, path_method_dictionary)
        swagger_data = add_examples_to_config_dtos(swagger_data)

        write_yaml_file(output_file_path, swagger_data)
        print('The process of adding examples is finished')
    else:
        print('File doesn\'t exist')


if __name__ == "__main__":
    # Fetch command-line arguments
    input_file_path = sys.argv[1] if len(sys.argv) > 1 else None
    output_file_path = sys.argv[2] if len(sys.argv) > 2 else None

    main(input_file_path, output_file_path)
