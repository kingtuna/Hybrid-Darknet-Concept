/* SSDP Service Emulator written by Achilleas Moustakis */

#include <stdbool.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <err.h>

int handle_datagram(char buffer[], int count){
        if (strstr(buffer,"M-SEARCH")!=NULL){
                return 1;
    }
    else{
        return -1;
    }
}

int main(){
        //Create child(deamon) process
        pid_t process_id = fork();
    if (process_id<0){
                printf("Fork failure!\n");
                exit(1);
        }
        else if (process_id>0){
                printf("Deamon process initialized!\n");
                printf("Terminating parent process...\n");
                exit(0);
        }

        //IP address and port converted from string to struct sockaddr_in
    const char* hostname="0.0.0.0"; /* wildcard */
    const char* portname="1900";
        struct addrinfo hints;
        struct addrinfo* res=0;
        int fd;

        //Content to reflect back
        const char content[]="HTTP/1.1 200 OK\r\nCache-Control: max-age=120\r\nLocation: http://192.168.0.1:65535/rootDesc.xml\r\nServer: Linux/2.4.22-1.2115.nptl UPnP/1.0 miniupnpd/1.0\r\nST: urn:schemas-upnp-org:device:InternetGatewayDevice:\r\nUSN: uuid:b1c5d60c-1dd1-11b2-8687-a0bc8f76d644::urn:schemas-upnp-org:device:InternetGatewayDevice:\r\n\r\nHTTP/1.1 200 OK\r\nCACHE-CONTROL: max-age = 120\r\nLOCATION: http://192.168.1.1:80/UPnP/IGD.xml\r\nST: urn:schemas-upnp-org:service:WANIPConnection:1\r\nSERVER: System/1.0 UPnP/1.0 IGD/1.0\r\nUSN: uuid:WANConnection{9679d566-230a-49d3-92e5-421e9223eaef}000000000000::urn:schemas-upnp-org:service:WANIPConnection:1\r\n\r\nHTTP/1.1 200 OK\r\nServer: Custom/1.0 UPnP/1.0 Proc/Ver\r\nLocation: http://192.168.1.1:5431/dyndev/uuid:204e7fce-118e-8e11-ce7f-4e204ece8e0000\r\nCache-Control:max-age=1800\r\nST:uuid:204e7fce-118e-8e11-ce7f-4e204ece8e0002\r\nUSN:uuid:204e7fce-118e-8e11-ce7f-4e204ece8e0002\r\n\r\nHTTP/1.1 200 OK\r\nCACHE-CONTROL: max-age = 120\r\nLOCATION: http://192.168.1.1:80/UPnP/IGD.xml\r\nST: urn:schemas-upnp-org:device:WANDevice:1\r\nSERVER: System/1.0 UPnP/1.0 IGD/1.0\r\nUSN: uuid:WAN{84807575-251b-4c02-954b-e8e2ba7216a9}000000000000::urn:schemas-upnp-org:device:WANDevice:1\r\n\r\n";
    unsigned int content_size=sizeof(content);
    char incoming_buffer[90];
    struct sockaddr_in src_addr;
    socklen_t src_addr_len;

        memset(&hints,0,sizeof(hints));
        hints.ai_family=AF_INET;
        hints.ai_socktype=SOCK_DGRAM;
        hints.ai_protocol=0;
        hints.ai_flags=AI_PASSIVE|AI_ADDRCONFIG;

        if (getaddrinfo(hostname,portname,&hints,&res)!=0) {
                printf("ERROR");
        }
        //Create socket
        fd=socket(res->ai_family,res->ai_socktype,res->ai_protocol);
        if (fd==-1) {
                printf("ERROR: socket");
        }
        //Bind socket
        if (bind(fd,res->ai_addr,res->ai_addrlen)==-1) {
                printf("ERROR: bind");
        }

    while(1){

        //Receive and handle datagrams
        if (recvfrom(fd,incoming_buffer,90,0,(struct sockaddr*)&src_addr,&src_addr_len)==-1) {
                        printf("ERROR: count=-1");
        }
        else {//Sending response
                if (strstr(incoming_buffer,"M-SEARCH")!=NULL){
                sendto(fd,content,content_size,0,(struct sockaddr*)&src_addr,src_addr_len);
            }
        }
        //memset(&buffer[0],0,sizeof(incoming_buffer));
    }
    close(fd);
    return 0;
}