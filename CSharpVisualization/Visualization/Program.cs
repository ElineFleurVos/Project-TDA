namespace ConsoleApp8
{
    using SFML.Graphics;
    using SFML.System;
    using System;
    using System.Collections.Specialized;
    using System.Globalization;
    using System.Net.NetworkInformation;

    namespace window_core
    {
        static class Program
        {
            static void Main(string[] args)
            {
                Console.WriteLine("Press ESC key to close window");
                var window = new SimpleWindow();
                window.Run();
            }
        }

        class Entry
        {
            public float Long;
            public float Lat;
            public float Alt;
            public Color c;
            public Vector2f pos;
        }

        public struct Line
        {
            public Color Color;
            public LinePoint[] Points;
            public Vertex[] lineverts;
        }

        public struct LinePoint
        {
            public float Long;
            public float Lat;
            public float Alt;

            public DateTime Time;
        }

        public class LineLoader
        {
            public static List<Vertex> vertices = new List<Vertex>();

            public static Line Load(string pltPath)
            {
                var lines = File.ReadAllLines(pltPath);
                var points = new List<LinePoint>();
                for (int i = 6; i < lines.Length; i++)
                {
                    var l = lines[i];
                    var split = l.Split(',');
                    points.Add(new LinePoint()
                    {
                        Long = float.Parse(split[0], CultureInfo.InvariantCulture),
                        Lat = float.Parse(split[1], CultureInfo.InvariantCulture),
                        Alt = float.Parse(split[2], CultureInfo.InvariantCulture),
                        Time = DateTime.Parse(split[5] + " " + split[6], CultureInfo.InvariantCulture),
                    });
                }

                Vertex[] verts = new Vertex[points.Count * 2];
                Color color = new Color((byte)Random.Shared.NextInt64(55), (byte)Random.Shared.NextInt64(155), (byte)Random.Shared.NextInt64(255), 20);
                for (int i = 0; i < points.Count - 1; i++)
                {

                    var p = points[i];
                    var p2 = points[i + 1];
                    if (SimpleWindow.Distance(p, p2) < .005f)
                    {
                        verts[i * 2].Position = SimpleWindow.ScaleLonglat(new Vector2f(p.Long, p.Lat));
                        verts[i * 2].Color = color;

                        verts[i * 2 + 1].Position = SimpleWindow.ScaleLonglat(new Vector2f(p2.Long, p2.Lat));
                        verts[i * 2 + 1].Color = color;
                    }

                    vertices.Add(verts[i * 2]);
                }


                return new Line()
                {
                    Color = color,
                    Points = points.ToArray(),
                    lineverts = verts,
                };
            }
        }

        class SimpleWindow
        {

            View view = new View();

            public static Vector2f ScaleLonglat(Vector2f longlat)
            {
                longlat -= new Vector2f(39.9742f, 116.3274f);
                longlat *= 1000f;
                return longlat;
            }

            public void Run()
            {
                var mode = new SFML.Window.VideoMode(1920 / 1, 1080 / 1);

                var window = new SFML.Graphics.RenderWindow(mode, "Beijing", SFML.Window.Styles.Default, new SFML.Window.ContextSettings()
                {
                    AntialiasingLevel = 8,
                });

                window.KeyPressed += Window_KeyPressed;

                var circle = new SFML.Graphics.CircleShape(20000f)
                {
                    FillColor = SFML.Graphics.Color.Blue
                };
                var shapes = new List<CircleShape>();
                var c = new Color(1, 1, 1);
                if (!Directory.Exists("Data") || Directory.GetFiles("Data", "*.plt", SearchOption.AllDirectories).Length == 0)
                    throw new Exception("Stop wat plt files in 'Data' folder");

                string[] array = Directory.GetFiles("Data", "*.plt", SearchOption.AllDirectories);
                List<Line> lines = new();

                for (int i = 0; i < array.Length / 10; i++)
                {
                    lines.Add(LineLoader.Load(array[i]));
                }

                var lps = new VertexBuffer((uint)LineLoader.vertices.Count, PrimitiveType.Points, VertexBuffer.UsageSpecifier.Dynamic);
                lps.Update(LineLoader.vertices.ToArray());
                window.SetKeyRepeatEnabled(false);
                window.KeyPressed += Window_KeyPressed1;
                window.KeyReleased += Window_KeyReleased;
                window.SetVerticalSyncEnabled(true);
                view.Size = ((Vector2f)window.Size);
                view.Center = new Vector2f(0, 0);
                while (window.IsOpen)
                {
                    window.DispatchEvents();
                    window.Clear();
                    window.SetView(view);
                    var circleShape = new CircleShape(10000.1f, 5);
                    var rect = new RectangleShape();
                    view.Move(dir * view.Size.X * .005f);
                    view.Zoom(1f + zoom * .05f);

                    if (false)
                    {
                        foreach (var l in lines)
                        {
                            circleShape.FillColor = l.Color;
                            foreach (var p in l.Points)
                            {
                                circleShape.Position = ScaleLonglat(new Vector2f(p.Long, p.Lat));
                                Vector2i sp = window.MapCoordsToPixel(circleShape.Position);
                                if (sp.X > 0 && sp.Y > 0 && sp.X < window.Size.X && sp.Y < window.Size.Y)
                                    window.Draw(circleShape);
                            }
                        }
                    }

                    foreach (var l in lines)
                    {
                     //      window.Draw(l.lineverts, PrimitiveType.Lines);
                    }
                    lps.Draw(window, RenderStates.Default);

                    window.Display();
                }
            }

            private void Window_KeyReleased(object? sender, SFML.Window.KeyEventArgs e)
            {
                if (e.Code == SFML.Window.Keyboard.Key.W)
                    dir -= new Vector2f(0, -1);
                if (e.Code == SFML.Window.Keyboard.Key.S)
                    dir -= new Vector2f(0, 1);
                if (e.Code == SFML.Window.Keyboard.Key.A)
                    dir -= new Vector2f(-1, 0);
                if (e.Code == SFML.Window.Keyboard.Key.D)
                    dir -= new Vector2f(1, 0);

                if (e.Code == SFML.Window.Keyboard.Key.Q)
                    zoom -= 1;
                if (e.Code == SFML.Window.Keyboard.Key.E)
                    zoom -= -1;
            }

            bool showTriangles = true;
            bool showConnections = true;
            Vector2f dir = new Vector2f(0, 0);
            float zoom = 0;
            private void Window_KeyPressed1(object? sender, SFML.Window.KeyEventArgs e)
            {
                if (e.Code == SFML.Window.Keyboard.Key.W)
                    dir += new Vector2f(0, -1);
                if (e.Code == SFML.Window.Keyboard.Key.S)
                    dir += new Vector2f(0, 1);
                if (e.Code == SFML.Window.Keyboard.Key.A)
                    dir += new Vector2f(-1, 0);
                if (e.Code == SFML.Window.Keyboard.Key.D)
                    dir += new Vector2f(1, 0);

                if (e.Code == SFML.Window.Keyboard.Key.Q)
                    zoom += 1;
                if (e.Code == SFML.Window.Keyboard.Key.E)
                    zoom += -1;

                if (e.Code == SFML.Window.Keyboard.Key.T)
                    showTriangles = !showTriangles;

                if (e.Code == SFML.Window.Keyboard.Key.R)
                    showConnections = !showConnections;


                var window = (SFML.Window.Window)sender;
                if (e.Code == SFML.Window.Keyboard.Key.Escape)
                {
                    window.Close();
                }
            }

            public static float Distance(LinePoint p1, LinePoint p2)
            {
                var xdiff = p1.Long - p2.Long;
                var ydiff = p1.Lat - p2.Lat;
                return MathF.Sqrt(xdiff * xdiff + ydiff * ydiff);
            }

            /// <summary>
            /// Function called when a key is pressed
            /// </summary>
            private void Window_KeyPressed(object sender, SFML.Window.KeyEventArgs e)
            {
              
            }
        }
    }
}