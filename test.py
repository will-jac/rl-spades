class a():
 def foo(self, x):
  self.x = 1 + x
 def bar(self, x):
  self.foo(x)
  print(x)
 def baz(self, x):
  self.bar(x)
  print(self.x)

obj = a()
obj.baz(10)