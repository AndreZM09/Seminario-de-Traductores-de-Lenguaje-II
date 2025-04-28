User {
  id: Integer,
  name: String &min(3)&max(50),
  email: String &email,
  tags?: [String]
}
