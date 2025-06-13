import os
import datetime
import logging

def check_file(file_path):
    """
    检测指定路径的文件并返回文件名和修改时间，保留相对路径
    
    参数:
        file_path (str): 文件的相对路径或完整路径
        
    返回:
        dict: 包含文件信息的字典，包括文件名、原始路径、是否存在和修改时间
    """
    logger = logging.getLogger(__name__)
    
    # 初始化结果字典，保留原始路径
    result = {
        "file_name": os.path.basename(file_path),
        "path": file_path,  # 保留原始路径（相对或绝对）
        "exists": False,
        "last_modified": None,
        "size_bytes": None,
        "is_dir": False
    }
    
    # 检查文件是否存在
    if os.path.exists(file_path):
        result["exists"] = True
        
        # 检查是否是目录
        if os.path.isdir(file_path):
            result["is_dir"] = True
            logger.info(f"路径 '{file_path}' 是一个目录")
        else:
            # 获取文件最后修改时间
            try:
                mod_time = os.path.getmtime(file_path)
                mod_time_dt = datetime.datetime.fromtimestamp(mod_time)
                result["last_modified"] = mod_time_dt.strftime("%Y-%m-%d %H:%M:%S")
                
                # 获取文件大小
                result["size_bytes"] = os.path.getsize(file_path)
                
                logger.info(f"文件 '{file_path}' 存在，最后修改时间: {result['last_modified']}")
            except OSError as e:
                logger.error(f"获取文件 '{file_path}' 信息时出错: {e}")
    else:
        logger.warning(f"文件 '{file_path}' 不存在")
    
    return result

def check_multiple_files(file_paths):
    """
    检测多个文件并返回它们的信息
    
    参数:
        file_paths (list): 文件路径列表
        
    返回:
        dict: 以文件路径为键，文件信息为值的字典
    """
    results = {}
    for file_path in file_paths:
        results[file_path] = check_file(file_path)
    return results
