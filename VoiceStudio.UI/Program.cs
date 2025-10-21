using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.FileProviders;
using Microsoft.Extensions.Hosting;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();

var app = builder.Build();
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
}

app.UseStaticFiles();

// Serve eval folder from ProgramData/VoiceStudio/eval at /eval
string baseDir;
var programDataEnv = Environment.GetEnvironmentVariable("PROGRAMDATA");
if (!string.IsNullOrWhiteSpace(programDataEnv)) baseDir = Path.Combine(programDataEnv, "VoiceStudio");
else
{
    var common = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
    baseDir = string.IsNullOrWhiteSpace(common) ? AppContext.BaseDirectory : Path.Combine(common, "VoiceStudio");
}
var evalDir = Path.Combine(baseDir, "eval");
Directory.CreateDirectory(evalDir);
app.UseStaticFiles(new StaticFileOptions
{
    FileProvider = new PhysicalFileProvider(evalDir),
    RequestPath = "/eval"
});

app.MapRazorPages();
app.Run();
