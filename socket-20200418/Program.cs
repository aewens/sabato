using System;
using System.Net;
using System.Net.Sockets;
using System.Text;

namespace socket_20200418
{
    class Program
    {
        public static string data = null;

        public static void StartListening() {
            byte[] bytes = new Byte[1024];

            IPHostEntry ipHostInfo = Dns.GetHostEntry(Dns.GetHostName());
            IPAddress ipAddress = ipHostInfo.AddressList[0];
            IPEndPoint localEndPoint = new IPEndPoint(ipAddress, 20202);

            Socket listener = new Socket(ipAddress.AddressFamily,
                SocketType.Stream, ProtocolType.Tcp);

            try {
                listener.Bind(localEndPoint);
                listener.Listen(10);

                Console.WriteLine("Waiting for a connection...");
                Socket handler = listener.Accept();

                while (true) {
                    data = null;

                    while (true) {
                        int bytesRec = handler.Receive(bytes);
                        data = data + Encoding.ASCII.GetString(bytes, 0,
                            bytesRec);

                        Console.Write(data);
                        if (data.IndexOf(".") > -1) {
                            break;
                        }
                    }

                    Console.WriteLine("Received: {0}", data);

                    byte[] message = Encoding.ASCII.GetBytes(data);
                    handler.Send(message);
                    //handler.Shutdown(SocketShutdown.Both);
                    //handler.Close();
                }
            } catch (Exception e) {
                Console.WriteLine(e.ToString());
            }

            Console.WriteLine("\nPress <Enter> to continue\n");
            Console.Read();
        }

        public static int Main(string[] args)
        {
            StartListening();
            return 0;
        }
    }
}
