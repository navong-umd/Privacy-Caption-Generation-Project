/*Application Package Name: com.tiktok.lite.go
class PRCS_377 {
/**
X.2UD;invoke(Ljava/lang/Object;)Ljava/lang/Object;
*/

    public final synthetic Object invoke(Object p20)
    {
        android.hardware.camera2.CameraDevice v8 = this.L;
        com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
        Object[] v9 = new Object[0];
        com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()V", "dzBzEgAjS8/YVFkiQFyGdpIIcIGkM9tlnBcBz8JkU7S83oC39JceYzy+GBSptlI1");
        if (!v3_1.preInvoke(100201, "android/hardware/camera2/CameraDevice", "close", v8, v9, "void", v10_1).intercept) {
            v8.close();
            v3_1.postInvoke(0, 100201, "android/hardware/camera2/CameraDevice", "close", v8, v9, v10_1, 1);
        } else {
            v3_1.postInvoke(0, 100201, "android/hardware/camera2/CameraDevice", "close", v8, v9, v10_1, 0);
        }
        return kotlin.Unit.L;
    }


}