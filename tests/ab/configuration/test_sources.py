# from ab.configuration.sources import (
#     convert_kwargs_source_to_task_definition,
# )


# def test_convert_kwargs_source_to_task_definition():
#     source_kwargs = dict(
#         identifier="TEST",
#         description="TEST",
#         url="https://example.com/",
#         filenames=["foo{STATION}.ext"],
#         destination="/tmp/autobernese",
#         parameters=dict(
#             station=["test"],
#             STATION=["TEST"],
#         ),
#     )

#     expected = dict(
#         identifier="TEST",
#         description="TEST",
#         arguments=dict(
#             url="https://example.com/",
#             filenames=["foo{STATION}.ext"],
#             destination="/tmp/autobernese",
#         ),
#         parameters=dict(
#             station=["test"],
#             STATION=["TEST"],
#         ),
#     )

#     result = convert_kwargs_source_to_task_definition(source_kwargs)
#     assert result == expected, f"Expected {result!r} to be {expected!r} ..."
