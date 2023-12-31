from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials


class GoogleSheetsClient:
    """
    Googlesheets Service Account Authenticated Api Client
    """

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    def __init__(
        self, credentials_path: str, spreadsheet_id: str = None, sheet_id: str = None
    ):
        credentials = Credentials.from_service_account_file(
            filename=credentials_path, scopes=self.scopes
        )
        service = build("sheets", "v4", credentials=credentials)
        self.speadsheets_engine = service.spreadsheets().values()
        self.spreadsheet_id = spreadsheet_id
        self.sheet_id = sheet_id

    def get_query_kwargs(
        self, range: str, spreadsheet_id: str = None, sheet_id: str = None
    ) -> dict:
        sheet_id = sheet_id or self.sheet_id
        spreadsheet_id = spreadsheet_id or self.spreadsheet_id
        if sheet_id:
            range = f"{self.sheet_id}!{range}"
        return {"spreadsheetId": spreadsheet_id, "range": range}

    def get_range(
        self, range: str, spreadsheet_id: str = None, sheet_id: str = None
    ) -> list:
        kwargs = self.get_query_kwargs(
            range, spreadsheet_id=spreadsheet_id, sheet_id=sheet_id
        )
        result = self.speadsheets_engine.get(**kwargs).execute()
        return result.get("values", list())

    def get_cell(self, cell: str, spreadsheet_id: str = None, sheet_id: str = None):
        values = self.get_range(
            range=cell, spreadsheet_id=spreadsheet_id, sheet_id=sheet_id
        )
        return values[0][0]

    def update_range(
        self, range: str, values: list, spreadsheet_id: str = None, sheet_id: str = None
    ) -> dict:
        kwargs = self.get_query_kwargs(
            range, spreadsheet_id=spreadsheet_id, sheet_id=sheet_id
        )
        kwargs.update(
            {
                "body": {"values": values},
                "valueInputOption": "USER_ENTERED",
            }
        )
        result = self.speadsheets_engine.update(**kwargs).execute()
        return result

    def update_cell(
        self, range: str, value, spreadsheet_id: str = None, sheet_id: str = None
    ) -> dict:
        return self.update_range(
            range=range,
            values=[[value]],
            spreadsheet_id=spreadsheet_id,
            sheet_id=sheet_id,
        )
