timestamp = `date -u +'%Y%m%d%H%M%S'`

change-version:
	@poetry version `poetry version -s | cut -f-3 -d.`.dev$(timestamp)
