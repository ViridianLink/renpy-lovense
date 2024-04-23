# RenPy Lovense Framework

## Getting Started

### QR Code
1. Set the variable `SERVER_URL` to the server URL.
2. [Optional] Set the variable `QR_CODE_ENDPOINT` to the endpoint for the QR code response.
3. [Optional] Set the variable `USERS_ENDPOINT` to the endpoint for obtaining the user.
4. Call either `LovenseDownloadQRCode()` action or `lovense.download_qr_code()` function to download the QR code.
    1. Player then scans the QR code with the Lovense app.
    2. Player details are then sent to the callback server url
5. Player details can be retrieved by calling `lovense.set_user()` function.
6. Call `LovenseRefresh()` action or `lovense.refresh()` function to refresh the user details and connected toys.
7. Use statements (or functions) in game to control the toys.

### Game Mode
1. Set the variable `lovense.local_ip` to the local IP address
2. Set the variable `lovense.http_port` to the port number
3. Call `LovenseRefresh()` action or `lovense.refresh()` function to refresh the user details and connected toys.
4. Use statements (or functions) in game to control the toys.

## Statements
- `lovense <action: str> <strength: int | float>`
    - `lovense vibrate 20`
    - `lovense rotate 20`
    - `lovense pump 3`
    - `lovense thrust 20`
    - `lovense finger 20`
    - `lovense suction 20`
    - `lovense depth 3`
    - `lovense all 1.0`

- `lovense stop`

## Actions
- `LovenseRefresh()`

- `LovenseDownloadQRCode()`

## Variables
- `SERVER_URL: str`

- `QR_CODE_ENDPOINT: str`

- `USERS_ENDPOINT: str`

- `lovense.local_ip: str`

- `lovense.http_port: str`

- `lovense.last_refresh: datetime.datetime`

- `lovense.server_online: bool`

- `lovense.status_message: str`

- `lovense.toys: dict[str, str]`

- `lovense.last_updated: int`

- `lovense.current_strengths: dict[LovenseAction, int]`

## Functions
- `lovense.send_function(actions: LovenseAction, strengths: Iterable[int] | float, time_sec: float = 0, stop_previous: bool = True) -> None:`

- `lovense.get_toys() -> None:`

- `lovense.vibrate(strength: Union[Sequence[int], int, float], time: float = 0, stop_previous: bool = True) -> None:`

- `lovense.rotate(strength: Union[Sequence[int], int, float], time: int = 0, stop_previous: bool = True) -> None:`

- `lovense.pump(strength: Union[Sequence[int], int, float], time: int = 0, stop_previous: bool = True) -> None:`

- `lovense.thrust(strength: Union[Sequence[int], int, float], time: int = 0, stop_previous: bool = True) -> None:`

- `lovense.finger(strength: Union[Sequence[int], int, float], time: int = 0, stop_previous: bool = True) -> None:`

- `lovense.suction(strength: Union[Sequence[int], int, float], time: int = 0, stop_previous: bool = True) -> None:`

- `lovense.depth(strength: Union[Sequence[int], int, float], time: int = 0, stop_previous: bool = True) -> None:`

- `lovense.all(strength: Union[Sequence[int], int, float], time: int = 0, stop_previous: bool = True) -> None:`

- `lovense.stop() -> None:`

- `lovense.get_server_status() -> bool:`

- `lovense.download_qr_code() -> None:`

- `lovense.set_user() -> None:`

- `lovense.refresh() -> None:`