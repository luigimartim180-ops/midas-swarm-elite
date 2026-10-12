.PHONY: test serve demo check clean

test:
	python3 -m pytest tests/ -q

check:
	node --check app/protocol.js
	python3 -c "import re,sys; h=open('app/index.html').read(); m=re.findall(r'<script>\n(.*?)\n</script>', h, re.S); open('/tmp/_app.js','w').write(m[0])"
	node --check /tmp/_app.js

serve:
	cd app && python3 -m http.server 12000

demo:
	python3 -m swarm.cli examples/profile.json

clean:
	rm -rf .pytest_cache **/__pycache__ /tmp/_app.js
