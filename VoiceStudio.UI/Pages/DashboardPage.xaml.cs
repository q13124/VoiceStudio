using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;
using System.Diagnostics;
using System.IO;

namespace VoiceStudio.UI.Pages
{
  public sealed partial class DashboardPage : Page
  {
    public DashboardPage(){ this.InitializeComponent(); }
    private void OnLaunch(object sender, RoutedEventArgs e)
    {
      try{
        var port = Port.Text?.Trim(); if(string.IsNullOrWhiteSpace(port)) port="5299";
        var tools = System.IO.Path.Combine(System.AppContext.BaseDirectory,"..","..","tools","run_dashboard.ps1");
        var psi = new ProcessStartInfo("powershell",$"-ExecutionPolicy Bypass -File \"{tools}\" -Port {port}");
        psi.Verb="runas"; psi.UseShellExecute=true;
        Process.Start(psi);
        Status.Text=$"Launching dashboard on http://localhost:{port}";
      }catch(Exception ex){ Status.Text=$"Error: {ex.Message}"; }
    }
  }
}
