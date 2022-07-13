from pathlib import Path

HERE = (Path(__file__) / "..").resolve()

def get_asset(name):
  print(name)
  return HERE / "data" / name
