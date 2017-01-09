/* License: Apache v2 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>

int main(int argc, char *argv[])
{
  int addrlen;
  int read_bytes = 0;
  u_int opt = 1;
  int fd, i;
  struct sockaddr_in local_addr;
  struct sockaddr_in remote_addr;
  struct ip_mreq req;
  char req_msg[] = {
    '@', 0x02, 0x00, 0x00, 0xb4, 'G', 'P', 'I', 'O', 0x02, '2', '5',
    0x08, 'f', 'u', 'n', 'c', 't', 'i', 'o', 'n', 0x03, 'o', 'u', 
    't', 0xff
  };
  char res_msg[128];

  if (argc < 2) {
    fprintf(stderr, "Usage: %s remote_ip\n", argv[0]);
    exit(1);
  }

  fd = socket(AF_INET, SOCK_DGRAM, 0);
  if (fd < 0) {
    perror("socket");
    exit(1);
  }

  setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
  
  memset(&local_addr, 0x00, sizeof(local_addr));
  memset(&remote_addr, 0x00, sizeof(remote_addr));
  memset(&req, 0x00, sizeof(req));
  memset(res_msg, 0x00, sizeof(res_msg));

  local_addr.sin_family = AF_INET;
  local_addr.sin_addr.s_addr = htonl(INADDR_ANY);
  local_addr.sin_port = htons(0);

  if (bind(fd, (struct sockaddr *)&local_addr, sizeof(local_addr)) < 0) {
    perror("bind");
    close(fd);
    exit(1);
  }

  remote_addr.sin_family = AF_INET;
  remote_addr.sin_addr.s_addr = inet_addr(argv[1]);
  remote_addr.sin_port = htons(5683);
  
  sendto(fd, req_msg, sizeof(req_msg), 0, 
	 (struct sockaddr *)&remote_addr, sizeof(remote_addr));
  fprintf(stdout, "Sent a message.\n");

  addrlen = sizeof(remote_addr);
  read_bytes = recvfrom(fd, res_msg, sizeof(res_msg), 0,
			(struct sockaddr *)&remote_addr, &addrlen);

  if (read_bytes > 0) {
    printf("Received response message from server:\n[");
    for (i = 0; i < read_bytes; i++) {
      printf("%02x ", (uint8_t)(res_msg[i] & 0xFF));
    }
    printf("]\n");
  }

  close(fd);

  return 0;
}




