#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(int argc,char *argv[]){
    if (argc < 4){
        fprintf(stderr, "Usage: %s <target_ip> <target_port> <packet_size>\n", argv[0]);
        return 1;
    }

    const char *port = argv[2];
    int packet_size = atoi(argv[3]);
    
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket creation failed");
        return 1;
    }

    struct sockaddr_in target_addr;
    memset(&target_addr, 0, sizeof(target_addr));
    target_addr.sin_family = AF_INET;
    target_addr.sin_port = htons(atoi(port));
    if (inet_pton(AF_INET, argv[1], &target_addr.sin_addr) <= 0) {
        perror("Invalid address/ Address not supported");
        close(sockfd);
        return 1;
    }
    char payload[512];
    memset(payload, 'A', sizeof(payload));
    int sent_count = 0;
    for (int i = 0; i < packet_count; i++) {
            ssize_t bytes_sent = sendto(
                sockfd,
                payload,
                sizeof(payload),
                0,
                (struct sockaddr *)&dest_addr,
                sizeof(dest_addr)
            );

            if (bytes_sent > 0) {
                sent_count++;
            }
    }

    
    printf("SENT_PACKETS:%d\n", sent_count);
    close(sockfd);
    return 0;
}