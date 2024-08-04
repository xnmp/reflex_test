
import hashlib
import random


class Hasher:
    
    all_hashes = set()
    
    @classmethod
    def generate(cls, input_string):
        seed = 1
        while (res:= cls.hash_string(input_string, seed=seed)) in cls.all_hashes:
            seed += 1
            if seed > 1000:
                raise Exception("Too many hashes generated")
        cls.all_hashes.add(res)
        return res
    
    @staticmethod
    def hash_string(input_string, seed=42):
        md5_hash = hashlib.md5()
        md5_hash.update(input_string.encode('utf-8'))
        hex_hash = md5_hash.hexdigest()
        random.seed(hex_hash + str(seed))
        char_set = '0123456789abcdefghijklmnopqrstuvwxyz'
        result = ''.join(random.choice(char_set) for _ in range(10))
        return result
