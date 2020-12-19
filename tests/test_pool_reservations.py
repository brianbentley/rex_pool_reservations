import rex_pool_reservations


def test_parse_config(mocker):
    mock_json = mocker.patch("json.load")
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data="{}"))
    test_config = "my_test_config.json"
    rex_pool_reservations.parse_config(test_config)
    mock_json.assert_called_once()
    mock_open.assert_called_once_with(test_config, "r")


def test_login(mocker):
    mock_web_driver = mocker.MagicMock()
    rex_pool_reservations.navigate_to_reservation_page(mock_web_driver)
    calls = [
        mocker.call("menu_SCH"),
        mocker.call().click(),
        mocker.call("dateControlText"),
        mocker.call().__bool__(),
        mocker.call("ui-datepicker-div"),
        mocker.call().__bool__(),
        mocker.call("ui-datepicker-div"),
        mocker.call().find_element_by_link_text("19"),
        mocker.call().find_element_by_link_text().click(),
        mocker.call("btnContinue"),
        mocker.call().click(),
    ]
    mock_web_driver.find_element_by_id.assert_has_calls(calls)
