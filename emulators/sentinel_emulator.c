/* Sentinel Amplification Emulator written by Achilleas Moustakis */

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
	if (strstr(buffer,"\x7A\x00\x00\x00\x00\x00")!=NULL){
        	//printf("Message received!\n");
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
		//printf("Deamon process initialized!\n");
		//printf("Terminating parent process...\n");
		exit(0);
	}

	//IP address and port converted from string to struct sockaddr_in
    	const char* hostname="0.0.0.0"; /* wildcard */
    	const char* portname="1900";
   	struct addrinfo hints;
	
	//Content to reflect back
   	char content[]="z,PSH,'A{^QOHpe])]\^cRH>%gNQXbH>1JRN[hKS$gMPfmeA{Z[`bkT[)h>AE";
    	while(1){
        	memset(&hints,0,sizeof(hints));
        	hints.ai_family=AF_INET;
        	hints.ai_socktype=SOCK_DGRAM;
        	hints.ai_protocol=0;
        	hints.ai_flags=AI_PASSIVE|AI_ADDRCONFIG;

        	struct addrinfo* res=0;
        	int err = getaddrinfo(hostname,portname,&hints,&res);
        	if (err!=0) {
            		printf("ERROR");
        }	
        //Create socket
        int fd=socket(res->ai_family,res->ai_socktype,res->ai_protocol);
        if (fd==-1) {
            	printf("ERROR: socket");
        }
        //Bind socket
        if (bind(fd,res->ai_addr,res->ai_addrlen)==-1) {
            	printf("ERROR: bind");
        }
        //Receive and handle datagrams
        char buffer[1549];
        struct sockaddr_in src_addr;
        socklen_t src_addr_len;
        ssize_t count;

        count = recvfrom(fd,buffer,sizeof(buffer),0,(struct sockaddr*)&src_addr,&src_addr_len);
        if (count==-1) {
            	printf("ERROR: count=-1");
        }
        else if (count==sizeof(buffer)) {
            	warn("datagram too large for buffer: truncated");
        }
        else {//Sending response
          	if (handle_datagram(buffer,count)==1){
               		sendto(fd,content,sizeof(content),0,(struct sockaddr*)&src_addr,src_addr_len);
            }
        }
        memset(&buffer[0],0,sizeof(buffer));
        close(fd);
    }
    return 0;
}

