"""
Example usage of `bytes`.
"""

bytes_array_1 = bytes(5)
# b'\x00\x00\x00\x00\x00'

bytes_array_2 = bytes([5])
# b'\x05'

bytes_array_2.decode()
# '\x05'

print(bytes_array_2)
# b'\x05'

print(bytes_array_2.decode())
# (Non-printable character. See https://condor.depaul.edu/sjost/lsp121/documents/ascii-npr.htm)

ord(bytes_array_2)
# 5

bytes_array_3 = bytes([151])
# b'\x97'

bytes_array_3.decode("cp1252")  # Available codes besides default "utf-8" and "cp1252" use here, are listed at https://docs.python.org/3/library/codecs.html#standard-encodings
# '—'

ord("—")
# 8212
