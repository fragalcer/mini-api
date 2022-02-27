from drf_yasg import openapi

seconds = openapi.Parameter(
    'seconds',
    openapi.IN_FORM,
    description="Amount of time in seconds in which the temporary_url will expire. (Only available for Enterprise "
                "users).",
    type=openapi.TYPE_STRING,
    format=openapi.FORMAT_DATETIME,
)
