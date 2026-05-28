/*Application Package Name: com.tiktok.lite.go
class PRCS_422 {
/**
X.7ud;L()I
*/

    public final int L()
    {
        com.ss.android.vesdklite.log.LELogcat.Log(2, "LECamera2", "camera2 startPreview");
        if (this.LBL != null) {
            try {
                int v0_0 = this.LIILL;
            } catch (android.hardware.camera2.CameraDevice v2_1) {
                com.ss.android.vesdklite.log.LELogcat.Log(4, "LECamera2", "Camera Access Exception: ".concat(String.valueOf(v2_1)));
                v2_1.printStackTrace();
                int v0_7 = this.LIII;
                v2_1.getMessage();
                v0_7.L();
                return -1;
            } catch (android.hardware.camera2.CameraDevice v2_0) {
                com.ss.android.vesdklite.log.LELogcat.Log(4, "LECamera2", "Camera startPreview Exception: ".concat(String.valueOf(v2_0)));
                v2_0.printStackTrace();
                int v0_4 = this.LIII;
                v2_0.getMessage();
                v0_4.L();
                return -1;
            }
            if ((v0_0 == 0) || (!v0_0.LD())) {
                com.ss.android.vesdklite.log.LELogcat.Log(4, "LECamera2", "FrameHolder is null or env is not ready yet");
                return -108;
            } else {
                int v7_0 = this.LIIIII.LB;
                int v8 = this.LIIIII.L;
                if ((this.LIILL.LF() == X.7OF.JAVA_IMAGE_READER) || (this.LIILL.LF() == X.7OF.NATIVE_IMAGE_READER)) {
                    if (this.LIILIIL.isOutputSupportedFor(34)) {
                        int v0_26 = X.7PN.L(X.7ud.L(this.LIILIIL.getOutputSizes(34)), new com.ss.android.vesdklite.record.camera.TEFrameSize(this.LIIIII.LB, this.LIIIII.L));
                        v7_0 = v0_26.L;
                        v8 = v0_26.LB;
                    } else {
                        com.ss.android.vesdklite.log.LELogcat.Log(3, "LECamera2", "Image format is not supported, fallback to TextureHolder");
                        this.LIILL.LFF();
                        if (!this.LIILL.LD()) {
                            com.ss.android.vesdklite.log.LELogcat.Log(4, "LECamera2", "FrameHolder is null or env is not ready yet");
                            return -108;
                        }
                    }
                }
                if (this.LIILL.L(v7_0, v8, this.LFF(), this.LIIIIZ)) {
                    android.hardware.camera2.CameraCaptureSession$StateCallback v1_8 = this.LIILL.LCCII();
                    this.LIILLL = v1_8;
                    if (this.LIILIIL.isOutputSupportedFor(v1_8)) {
                        java.util.ArrayList v5_4 = new java.util.ArrayList();
                        v5_4.add(this.LIILLL);
                        android.hardware.camera2.CameraCaptureSession$StateCallback v1_9 = this.LBL.createCaptureRequest(3);
                        this.LC = v1_9;
                        v1_9.addTarget(this.LIILLL);
                        this.LF();
                        this.LBL.createCaptureSession(v5_4, this.LIILZZLLZ, this.LIILII);
                        com.ss.android.vesdklite.log.LELogcat.Log(1, "LECamera2", "mCameraDevice.createCaptureSession successfully");
                        return 0;
                    } else {
                        com.ss.android.vesdklite.log.LELogcat.Log(3, "LECamera2", "Surface is not supported");
                        return -118;
                    }
                } else {
                    com.ss.android.vesdklite.log.LELogcat.Log(3, "LECamera2", "Failed to start frame holder");
                    return -117;
                }
            }
        } else {
            com.ss.android.vesdklite.log.LELogcat.Log(4, "LECamera2", "CameraDevice is null");
            this.LFF = 1;
            return -108;
        }
    }


}