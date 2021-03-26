from ..lambdas.hello_world.src.app import handler


def When_the_handler_function_is_invoked__Then_it_returns_a_response():
    assert "Hello" in handler(None, None)
