from werkzeug.security import generate_password_hash
#USE TO GENERATE PASSWORD HASHES FOR DB TESTING
print()
hash_value = generate_password_hash("agent2")
print(hash_value)
