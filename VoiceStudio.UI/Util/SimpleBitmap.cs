using Microsoft.UI.Xaml.Media.Imaging;
using System;
using System.Runtime.InteropServices.WindowsRuntime;

namespace VoiceStudio.UI.Util
{
  public static class SimpleBitmap
  {
    public static WriteableBitmap Make(int w,int h, byte[] bgra32)
    {
      var bmp = new WriteableBitmap(w,h);
      using var s = bmp.PixelBuffer.AsStream();
      s.Write(bgra32,0,bgra32.Length);
      bmp.Invalidate();
      return bmp;
    }
  }
}
