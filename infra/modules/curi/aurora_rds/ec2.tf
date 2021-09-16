resource "aws_key_pair" "db_key" {
  key_name   = "db_key_pair"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCvbfxaZDpyeCsJTIVd48Fao5Lt/El/Vj6O+Vp7CZvR4o9+xgB77FmULhyq3y7/LNHmGAKyU6NeXMYw2q0lcw7bdgpxXOdXys4mAatY12m9SbEt9wzsBpmIgK/6yEryI2qvlpp5Md+oXtDAcM5BqI2zckV0aWMdWirxu6u+xQOyQxGKkaK4JOwkkXWQqEBd8sz3M+Owao7i0r1P3WVaaTdoz2mGdZOdW/AvyLJbqv6wUx1llueKrztVR9NtiwJxmkNiXr0vXEIwR9bz+mR9XKDr9DLtgL3cPLV7Am8UOTmNUMrSvztutF1OThCUuyGfNemTTFXtTwNQwVxBnoit5tKnOTyHQFH4+R/zxPWgSpgOz1NybLP5O+y/jNScHgjp/nFqAvBkSXdbhTwBvEhrZNJ7nKxTE8Fs+5f9j7veC1v9jM8ol4r7AePaiPBq3P/0U98WSGRhEmLTkred63hdij1tWQflgI9DxXKuyRclMOOT349OX7N15Tjr+uoq8HE5VKs= lucipak@Lucis-MacBook-Pro.local"
}
resource "aws_instance" "ec2" {
  ami                         = "ami-087c17d1fe0178315"
  associate_public_ip_address = true
  instance_type               = "t2.micro"
  key_name                    = aws_key_pair.db_key.key_name
  subnet_id                   = aws_default_subnet.default_subnet_a.id

  vpc_security_group_ids = [aws_default_vpc.default_vpc.default_security_group_id]

  tags = local.tags

}
