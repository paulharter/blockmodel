

class BaseModelReader(object):

    def get(self, x, y, z):
        return 0, 0

    def check_size(self, max_size):
        if max_size is not None:
            if self.width > max_size or self.height > max_size or self.depth > max_size:
                raise Exception("Model too big, max is %s" % max_size)