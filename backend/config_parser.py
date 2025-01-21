import configparser
import os
import logging

# Configure logging
logger = logging.getLogger("config_logger")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

def read_config(file_path):
    config = configparser.ConfigParser()
    config_values = {}

    try:
        # Check if the config file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        # Read the config file
        config.read(file_path)
        
        if not config.sections():
            raise ValueError(f"No sections found in the config file: {file_path}")

        # Parse config sections and values
        for section in config.sections():
            section_dict = {}
            for key, value in config.items(section):
                # Convert boolean values properly
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                section_dict[key] = value
            config_values[section] = section_dict

        logger.info(f"Configuration file '{file_path}' successfully read.")
    
    except FileNotFoundError as fnf_error:
        logger.error(fnf_error)
        raise
    
    except ValueError as ve:
        logger.error(f"Error reading config file: {ve}")
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error occurred while reading config file: {e}")
        raise
    
    return config_values

def set_env_variables(config_values):
    try:
        for section, values in config_values.items():
            for key, value in values.items():
                env_var_name = f"{section.upper()}_{key.upper()}"
                os.environ[env_var_name] = str(value)
                logger.info(f"Environment variable '{env_var_name}' set to '{value}'")
    
    except Exception as e:
        logger.error(f"Error setting environment variables: {e}")
        raise
