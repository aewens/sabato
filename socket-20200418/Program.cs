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

                while (true) {
                    Console.WriteLine("Waiting for a connection...");
                }
            } catch (Exception e) {
                Console.WriteLine(e.ToString());
            }
        }

        public static int Main(string[] args)
        {
            Console.WriteLine("Hello World!");
            return 0;
        }
    }
}
