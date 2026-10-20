"""Download the UCI Cleveland heart disease file and write the cleaned CSV."""
from heart import config, data


def main() -> None:
    raw = data.download_raw(config.RAW_PATH)
    df = data.clean(data.load_raw(raw))
    config.CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.CLEAN_PATH, index=False)
    print(f"raw   -> {raw}")
    print(f"clean -> {config.CLEAN_PATH}  rows={len(df)}  cols={df.shape[1]}")
    print("missing values:\n" + df.isna().sum()[lambda s: s > 0].to_string())
    print("class balance:\n" + df[config.TARGET].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
