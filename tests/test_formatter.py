from datadog_api_client_generator.openapi.formatter import snake_case, camel_case


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


def test_camel_case():
    assert camel_case("foo") == "Foo"
    assert camel_case("foo bar") == "FooBar"
    assert camel_case("FooBar") == "FooBar"
    assert camel_case("fooBarBaz") == "FooBarBaz"
    assert camel_case("fooBARBaz") == "FooBarBaz"
    assert camel_case("foo  bar") == "FooBar"
    assert camel_case("Foo__Bar") == "FooBar"
    assert camel_case("FooBar_") == "FooBar"
    assert camel_case("FooBar ") == "FooBar"