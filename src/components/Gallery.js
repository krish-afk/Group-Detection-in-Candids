import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import JSZip from "jszip";
import "./Gallery.css";

export default function Gallery() {
    const location = useLocation();
    const zipBlob = location.state?.zipBlob;

    const [folders, setFolders] = useState([]);
    const [selectedFolder, setSelectedFolder] = useState(null);
    const [images, setImages] = useState([]);

    useEffect(() => {
        if (zipBlob) {
            const zip = new JSZip();
            zip.loadAsync(zipBlob).then((unzipped) => {
                const folderNames = Object.keys(unzipped.files).reduce((acc, filePath) => {
                    const folder = filePath.split("/")[0];
                    if (folder !== ".DS_Store" && !acc.includes(folder)) acc.push(folder);
                    return acc;
                }, []);
                setFolders(folderNames);
            });
        }
    }, [zipBlob]);

    const handleFolderSelect = async (folderName) => {
        setSelectedFolder(folderName);
        const zip = new JSZip();
        const unzipped = await zip.loadAsync(zipBlob);
        const folderFiles = Object.keys(unzipped.files).filter((file) => file.startsWith(folderName + "/") && !file.endsWith("/"));
        
        const imagePromises = folderFiles.map(async (file) => {
            const imageBlob = await unzipped.files[file].async("blob");
            return URL.createObjectURL(imageBlob);
        });

        const imageUrls = await Promise.all(imagePromises);
        setImages(imageUrls);
    };

    return (
        <div className="gallery-container">
            <h2>Select a Folder</h2>
            <div className="folder-list">
                {folders.map((folder) => (
                    <button key={folder} onClick={() => handleFolderSelect(folder)} className="folder-button">
                        {folder}
                    </button>
                ))}
            </div>

            {selectedFolder && (
                <div>
                    <h3>Images in {selectedFolder}</h3>
                    <div className="image-gallery">
                        {images.map((src, index) => (
                            <img key={index} src={src} alt={`Preview ${index}`} className="preview-image" />
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
