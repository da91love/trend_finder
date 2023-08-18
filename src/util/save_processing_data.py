def save_processing_data(progress: int, goal: int, input_file_path: str, output_file_path: str):
    if (progress_rate >= (cached_progress_rate + 20)) or (_.last(keywords) == keyword):
        # concat with existing data
        db = FsUtil.open_csv_2_json_file(root_path + DISCOVERED_BRAND_PATH)
        db += brands

        # save the file
        FsUtil.save_json_2_csv_file(db, root_path + DISCOVERED_BRAND_PATH)

        # update progress_rate
        cached_progress_rate = progress / len(keywords) * 100

        # initiate brands
        brands = []

        # log
        logger.debug(FILE_SAVE_SUCCESS_MSG)
