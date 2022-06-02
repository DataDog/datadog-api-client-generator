from datadog_api_client_generator.formatter import snake_case


def test_snake_case():
    assert snake_case("foo") == "foo"
    assert snake_case("foo bar") == "foo_bar"
    assert snake_case("FooBar") == "foo_bar"
    assert snake_case("fooBarBaz") == "foo_bar_baz"
    assert snake_case("fooBARBaz") == "foo_bar_baz"
    assert snake_case("foo  bar") == "foo_bar"
    assert snake_case("Foo__Bar") == "foo_bar"
    assert snake_case("FooBar_") == "foo_bar"
    assert snake_case("FooBar ") == "foo_bar"
