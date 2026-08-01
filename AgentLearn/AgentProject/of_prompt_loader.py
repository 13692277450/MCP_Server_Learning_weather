from of_path_tool import get_abs_path
from of_config_handler import prompts_conf
from of_logger_handler import logger

def load_system_prompts():
    try:
        system_prompt_path = get_abs_path(prompts_conf['main_prompt_path'])
    except Exception as e:
        logger.error(f"[load_system_promptes] 在yml配置里面没有main_prompt_path配置项Error loading system prompt")
        raise e

    try:
        return open(system_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_system_promptes] 读取system_prompt文件失败Error loading system prompt{str(e)}")
        raise e
    

    
def load_rag_prompts():
    try:
        rag_prompt_path = get_abs_path(prompts_conf['rag_summarize_prompt_path'])
    except Exception as e:
        logger.error(f"[load_rag_promptes] 在yml配置里面没有rag_summarize_prompt_path配置项Error loading rag_summarize prompt")
        raise e

    try:
        return open(rag_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_rag_promptes] 读取rag_summarize_prompt文件失败Error loading rag_summarize prompt{str(e)}")
        raise e
    
def load_report_prompts():
    try:
        report_prompt_path = get_abs_path(prompts_conf['report_prompt_path'])
    except Exception as e:
        logger.error(f"[load_report_promptes] 在yml配置里面没有report_prompt_path配置项Error loading report prompt")
        raise e

    try:
        return open(report_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_report_promptes] 读取report_prompt文件失败Error loading report prompt{str(e)}")
        raise e
    
if __name__ == "__main__":
    print(load_rag_prompts())