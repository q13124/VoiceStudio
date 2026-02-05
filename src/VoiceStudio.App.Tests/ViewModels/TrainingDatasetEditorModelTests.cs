using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Collections.Generic;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Tests.ViewModels
{
    [TestClass]
    public class TrainingDatasetEditorModelTests
    {
        #region DatasetDetail Model Tests

        [TestMethod]
        public void DatasetDetail_DefaultValues()
        {
            var detail = new DatasetDetail();

            Assert.AreEqual(string.Empty, detail.Id);
            Assert.AreEqual(string.Empty, detail.Name);
            Assert.IsNull(detail.Description);
            Assert.IsNotNull(detail.AudioFiles);
            Assert.AreEqual(0, detail.AudioFiles.Count);
            Assert.AreEqual(0.0, detail.TotalDuration);
            Assert.AreEqual(0, detail.TotalFiles);
            Assert.AreEqual(string.Empty, detail.Created);
            Assert.AreEqual(string.Empty, detail.Modified);
        }

        [TestMethod]
        public void DatasetDetail_PropertiesSetCorrectly()
        {
            var audioFiles = new List<DatasetAudioFile>
            {
                new DatasetAudioFile { Id = "af1" }
            };

            var detail = new DatasetDetail
            {
                Id = "dataset123",
                Name = "Training Dataset",
                Description = "Voice samples for training",
                AudioFiles = audioFiles,
                TotalDuration = 3600.5,
                TotalFiles = 100,
                Created = "2026-01-01",
                Modified = "2026-01-15"
            };

            Assert.AreEqual("dataset123", detail.Id);
            Assert.AreEqual("Training Dataset", detail.Name);
            Assert.AreEqual("Voice samples for training", detail.Description);
            Assert.AreSame(audioFiles, detail.AudioFiles);
            Assert.AreEqual(3600.5, detail.TotalDuration);
            Assert.AreEqual(100, detail.TotalFiles);
            Assert.AreEqual("2026-01-01", detail.Created);
            Assert.AreEqual("2026-01-15", detail.Modified);
        }

        #endregion

        #region DatasetAudioFile Model Tests

        [TestMethod]
        public void DatasetAudioFile_DefaultValues()
        {
            var audioFile = new DatasetAudioFile();

            Assert.AreEqual(string.Empty, audioFile.Id);
            Assert.AreEqual(string.Empty, audioFile.AudioId);
            Assert.IsNull(audioFile.Transcript);
            Assert.IsNull(audioFile.Duration);
            Assert.IsNull(audioFile.SampleRate);
            Assert.AreEqual(0, audioFile.Order);
            Assert.AreEqual(string.Empty, audioFile.Created);
        }

        [TestMethod]
        public void DatasetAudioFile_PropertiesSetCorrectly()
        {
            var audioFile = new DatasetAudioFile
            {
                Id = "af123",
                AudioId = "audio456",
                Transcript = "Hello world",
                Duration = 5.5,
                SampleRate = 44100,
                Order = 1,
                Created = "2026-01-01"
            };

            Assert.AreEqual("af123", audioFile.Id);
            Assert.AreEqual("audio456", audioFile.AudioId);
            Assert.AreEqual("Hello world", audioFile.Transcript);
            Assert.AreEqual(5.5, audioFile.Duration);
            Assert.AreEqual(44100, audioFile.SampleRate);
            Assert.AreEqual(1, audioFile.Order);
            Assert.AreEqual("2026-01-01", audioFile.Created);
        }

        #endregion

        #region DatasetDetailItem Model Tests

        [TestMethod]
        public void DatasetDetailItem_CreatedFromDetail()
        {
            var detail = new DatasetDetail
            {
                Id = "d1",
                Name = "Test Dataset",
                Description = "Test description",
                AudioFiles = new List<DatasetAudioFile>
                {
                    new DatasetAudioFile { Id = "af1" }
                },
                TotalDuration = 120.5,
                TotalFiles = 10,
                Created = "2026-01-01",
                Modified = "2026-01-02"
            };

            var item = new DatasetDetailItem(detail);

            Assert.AreEqual("d1", item.Id);
            Assert.AreEqual("Test Dataset", item.Name);
            Assert.AreEqual("Test description", item.Description);
            Assert.AreEqual(1, item.AudioFiles.Count);
            Assert.AreEqual(120.5, item.TotalDuration);
            Assert.AreEqual(10, item.TotalFiles);
            Assert.AreEqual("2026-01-01", item.Created);
            Assert.AreEqual("2026-01-02", item.Modified);
        }

        [TestMethod]
        public void DatasetDetailItem_DurationDisplay_FormatsCorrectly()
        {
            var detail = new DatasetDetail { TotalDuration = 123.456 };
            var item = new DatasetDetailItem(detail);

            Assert.AreEqual("123.46s", item.DurationDisplay);
        }

        [TestMethod]
        public void DatasetDetailItem_DurationDisplay_Zero()
        {
            var detail = new DatasetDetail { TotalDuration = 0 };
            var item = new DatasetDetailItem(detail);

            Assert.AreEqual("0.00s", item.DurationDisplay);
        }

        [TestMethod]
        public void DatasetDetailItem_FilesDisplay_FormatsCorrectly()
        {
            var detail = new DatasetDetail { TotalFiles = 50 };
            var item = new DatasetDetailItem(detail);

            Assert.AreEqual("50 files", item.FilesDisplay);
        }

        [TestMethod]
        public void DatasetDetailItem_FilesDisplay_ZeroFiles()
        {
            var detail = new DatasetDetail { TotalFiles = 0 };
            var item = new DatasetDetailItem(detail);

            Assert.AreEqual("0 files", item.FilesDisplay);
        }

        [TestMethod]
        public void DatasetDetailItem_AudioFilesConvertedToObservableCollection()
        {
            var detail = new DatasetDetail
            {
                AudioFiles = new List<DatasetAudioFile>
                {
                    new DatasetAudioFile { Id = "1" },
                    new DatasetAudioFile { Id = "2" },
                    new DatasetAudioFile { Id = "3" }
                }
            };
            var item = new DatasetDetailItem(detail);

            Assert.AreEqual(3, item.AudioFiles.Count);
        }

        #endregion

        #region DatasetAudioFileItem Model Tests

        [TestMethod]
        public void DatasetAudioFileItem_CreatedFromAudioFile()
        {
            var audioFile = new DatasetAudioFile
            {
                Id = "af1",
                AudioId = "audio1",
                Transcript = "Test transcript",
                Duration = 3.5,
                SampleRate = 22050,
                Order = 5,
                Created = "2026-01-01"
            };

            var item = new DatasetAudioFileItem(audioFile);

            Assert.AreEqual("af1", item.Id);
            Assert.AreEqual("audio1", item.AudioId);
            Assert.AreEqual("Test transcript", item.Transcript);
            Assert.AreEqual(3.5, item.Duration);
            Assert.AreEqual(22050, item.SampleRate);
            Assert.AreEqual(5, item.Order);
            Assert.AreEqual("2026-01-01", item.Created);
        }

        [TestMethod]
        public void DatasetAudioFileItem_DurationDisplay_WithDuration()
        {
            var audioFile = new DatasetAudioFile { Duration = 5.75 };
            var item = new DatasetAudioFileItem(audioFile);

            Assert.AreEqual("5.75s", item.DurationDisplay);
        }

        [TestMethod]
        public void DatasetAudioFileItem_DurationDisplay_NullDuration()
        {
            var audioFile = new DatasetAudioFile { Duration = null };
            var item = new DatasetAudioFileItem(audioFile);

            // The display should show "Unknown" or localized equivalent
            Assert.IsNotNull(item.DurationDisplay);
        }

        [TestMethod]
        public void DatasetAudioFileItem_NullablePropertiesAllowNull()
        {
            var audioFile = new DatasetAudioFile
            {
                Id = "af1",
                Transcript = null,
                Duration = null,
                SampleRate = null
            };

            var item = new DatasetAudioFileItem(audioFile);

            Assert.IsNull(item.Transcript);
            Assert.IsNull(item.Duration);
            Assert.IsNull(item.SampleRate);
        }

        #endregion
    }
}
