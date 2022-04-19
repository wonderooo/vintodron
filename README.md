# vintodron
1. w folderach discord i selenium po pobraniu zmienic nazwę plików env na .env
2. zamienic discord token w .env w folderze discord na ten otrzymany
3. pobrac docker
4. w glownym folderze wykonac polecenie <code>docker-compose up -d --build mongo</code>
5. nastepnie <code>docker exec -it mongo bash</code>
6. <code>mongo</code>
7. <code>use vinted</code>
8. <code>db.createUser({user: "kacpers", pwd: "vinted1234", roles: [{role: "readWrite", db: "vinted"}]})</code>
9. <code>exit</code>
10. <code>exit</code>
11. <code>docker-compose down</code>
12. <code>docker-compose up -d --build</code>
13. koniec :)
