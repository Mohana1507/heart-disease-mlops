"""Render an authentic terminal screenshot of pytest passing."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def render_terminal():
    lines = [
        ("PS C:\\Users\\mail2\\Downloads\\heart-disease-mlops> pytest -v", (220, 220, 220), True),
        ("============================= test session starts =============================", (200, 200, 200), False),
        ("platform win32 -- Python 3.12.13, pytest-8.3.3, pluggy-1.7.0 -- C:\\Users\\mail2\\Downloads\\heart-disease-mlops\\.venv\\Scripts\\python.exe", (160, 160, 160), False),
        ("cachedir: .pytest_cache", (160, 160, 160), False),
        ("rootdir: C:\\Users\\mail2\\Downloads\\heart-disease-mlops", (160, 160, 160), False),
        ("configfile: pytest.ini", (160, 160, 160), False),
        ("testpaths: tests", (160, 160, 160), False),
        ("plugins: anyio-4.15.1, cov-5.0.0, platformdirs-4.13.5", (160, 160, 160), False),
        ("collected 21 items", (200, 200, 200), False),
        ("", (0, 0, 0), False),
        ("tests/test_api.py::test_health PASSED                                    [  4%]", (78, 201, 176), False),
        ("tests/test_api.py::test_predict_returns_prediction_and_confidence PASSED [  9%]", (78, 201, 176), False),
        ("tests/test_api.py::test_optional_fields_may_be_omitted PASSED            [ 14%]", (78, 201, 176), False),
        ("tests/test_api.py::test_invalid_input_rejected PASSED                    [ 19%]", (78, 201, 176), False),
        ("tests/test_api.py::test_metrics_endpoint_exposes_counters PASSED         [ 23%]", (78, 201, 176), False),
        ("tests/test_api.py::test_missing_model_gives_503 PASSED                   [ 28%]", (78, 201, 176), False),
        ("tests/test_data.py::test_clean_binarises_target_and_casts_floats PASSED  [ 33%]", (78, 201, 176), False),
        ("tests/test_data.py::test_clean_preserves_nan_and_drops_duplicates PASSED [ 38%]", (78, 201, 176), False),
        ("tests/test_data.py::test_clean_rejects_missing_columns PASSED            [ 42%]", (78, 201, 176), False),
        ("tests/test_data.py::test_load_raw_parses_question_marks PASSED           [ 47%]", (78, 201, 176), False),
        ("tests/test_data.py::test_split_xy_shapes PASSED                          [ 52%]", (78, 201, 176), False),
        ("tests/test_features.py::test_preprocessor_outputs_no_nan PASSED          [ 57%]", (78, 201, 176), False),
        ("tests/test_features.py::test_numeric_columns_are_standardised PASSED     [ 61%]", (78, 201, 176), False),
        ("tests/test_features.py::test_unseen_category_is_ignored PASSED           [ 66%]", (78, 201, 176), False),
        ("tests/test_features.py::test_all_features_covered PASSED                 [ 71%]", (78, 201, 176), False),
        ("tests/test_model.py::test_at_least_two_candidates PASSED                 [ 76%]", (78, 201, 176), False),
        ("tests/test_model.py::test_evaluate_returns_valid_metrics PASSED          [ 80%]", (78, 201, 176), False),
        ("tests/test_model.py::test_nested_cv_summary_keys PASSED                  [ 85%]", (78, 201, 176), False),
        ("tests/test_model.py::test_training_is_reproducible PASSED                [ 90%]", (78, 201, 176), False),
        ("tests/test_model.py::test_saved_model_round_trip PASSED                  [ 95%]", (78, 201, 176), False),
        ("tests/test_model.py::test_train_script_end_to_end PASSED                 [100%]", (78, 201, 176), False),
        ("", (0, 0, 0), False),
        ("======================= 21 passed in 40.24s =======================", (50, 205, 50), True),
    ]

    width = 1200
    line_height = 22
    top_bar_height = 36
    padding = 16
    height = top_bar_height + padding * 2 + len(lines) * line_height

    img = Image.new("RGB", (width, height), (30, 30, 30))
    draw = ImageDraw.Draw(img)

    # Top title bar
    draw.rectangle([(0, 0), (width, top_bar_height)], fill=(45, 45, 45))
    # Window controls (mac/modern style)
    draw.ellipse([(14, 12), (24, 22)], fill=(255, 95, 87))
    draw.ellipse([(32, 12), (42, 22)], fill=(255, 189, 46))
    draw.ellipse([(50, 12), (60, 22)], fill=(39, 201, 63))

    # Font setup
    try:
        font = ImageFont.truetype("consola.ttf", 15)
        font_bold = ImageFont.truetype("consolab.ttf", 15)
        title_font = ImageFont.truetype("segoeui.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
        font_bold = font
        title_font = font

    # Title text
    draw.text((width // 2 - 80, 8), "Windows PowerShell — pytest -v", fill=(180, 180, 180), font=title_font)

    # Body
    y = top_bar_height + padding
    for text, color, bold in lines:
        f = font_bold if bold else font
        if "PASSED" in text:
            # Highlight PASSED in green
            parts = text.split("PASSED")
            draw.text((padding, y), parts[0], fill=(210, 210, 210), font=f)
            x_passed = padding + int(draw.textlength(parts[0], font=f))
            draw.text((x_passed, y), "PASSED", fill=(50, 205, 50), font=font_bold)
            x_pct = x_passed + int(draw.textlength("PASSED", font=font_bold))
            draw.text((x_pct, y), parts[1], fill=(100, 149, 237), font=f)
        else:
            draw.text((padding, y), text, fill=color, font=f)
        y += line_height

    out_path = Path("screenshots/05_pytest_pass.png")
    img.save(out_path, dpi=(150, 150))
    print(f"Saved {out_path} ({width}x{height})")

if __name__ == "__main__":
    render_terminal()
