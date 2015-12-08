

DJSOLVER_TEMPLATE_TYPES = (('J', 'Jinja Template'),
                           ('M', 'Markdown')
                           )

DJSOLVER_TEMPLATE_FILENAME = 'djsl_templ'

DJSOLVER_CODE_FILENAME = 'djsl_py'

DJSOLVER_KEYWORD_SEPARATOR = ','


DJSOLVER_RESTRICTIONS_GLOBAL = {
                                'MAX_PROCESSES': 2,
                                'MAX_EXECUTION_TIME': 600,
                                'MAX_FIELD_LENGTH': 10000,
                                'MAX_FILE_SIZE': '1M',
                                }

DJSOLVER_TEXTINPUT_PREFIX = 'djs_inputs'

DJSOLVER_DATA_DELIMITER = ','
DJSOLVER_DATA_ROW_DELIMITER = '\n'