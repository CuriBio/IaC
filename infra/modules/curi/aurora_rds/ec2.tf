
resource "aws_instance" "ec2" {
  ami                         = "ami-087c17d1fe0178315"
  associate_public_ip_address = true
  instance_type               = "t2.micro"
  key_name                    = var.key_pair_name
  subnet_id                   = aws_default_subnet.default_subnet_a.id

  vpc_security_group_ids = [aws_default_vpc.default_vpc.default_security_group_id]

  tags = local.tags

}
