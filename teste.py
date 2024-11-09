from postgrest import SyncPostgrestClient


pg = SyncPostgrestClient("http://201.23.18.37:8080", schema="eduassist")

dt = pg.from_("questoes_gemini").select("*").execute()

print(dt)
