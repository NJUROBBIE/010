// 五子棋.cpp : 定义应用程序的入口点。
//

#include "framework.h"
#include "五子棋.h"

#define MAX_LOADSTRING 100

// 全局变量:
int hmtw = 5;//How many to win
HINSTANCE hInst;                                // 当前实例
WCHAR szTitle[MAX_LOADSTRING];                  // 标题栏文本
WCHAR szWindowClass[MAX_LOADSTRING];
// 主窗口类名

// 此代码模块中包含的函数的前向声明:
ATOM                MyRegisterClass(HINSTANCE hInstance);
BOOL                InitInstance(HINSTANCE, int);
LRESULT CALLBACK    WndProc(HWND, UINT, WPARAM, LPARAM);
INT_PTR CALLBACK    About(HWND, UINT, WPARAM, LPARAM);

int APIENTRY wWinMain(_In_ HINSTANCE hInstance,
                     _In_opt_ HINSTANCE hPrevInstance,
                     _In_ LPWSTR    lpCmdLine,
                     _In_ int       nCmdShow)
{
    UNREFERENCED_PARAMETER(hPrevInstance);
    UNREFERENCED_PARAMETER(lpCmdLine);

    // TODO: 在此处放置代码。

    // 初始化全局字符串
    LoadStringW(hInstance, IDS_APP_TITLE, szTitle, MAX_LOADSTRING);
    LoadStringW(hInstance, IDC_MY, szWindowClass, MAX_LOADSTRING);
    MyRegisterClass(hInstance);

    // 执行应用程序初始化:
    if (!InitInstance (hInstance, nCmdShow))
    {
        return FALSE;
    }

    HACCEL hAccelTable = LoadAccelerators(hInstance, MAKEINTRESOURCE(IDC_MY));

    MSG msg;

    // 主消息循环:
    while (GetMessage(&msg, nullptr, 0, 0))
    {
        if (!TranslateAccelerator(msg.hwnd, hAccelTable, &msg))
        {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }
    }

    return (int) msg.wParam;
}



//
//  函数: MyRegisterClass()
//
//  目标: 注册窗口类。
//
ATOM MyRegisterClass(HINSTANCE hInstance)
{
    WNDCLASSEXW wcex;

    wcex.cbSize = sizeof(WNDCLASSEX);

    wcex.style          = CS_HREDRAW | CS_VREDRAW;
    wcex.lpfnWndProc    = WndProc;
    wcex.cbClsExtra     = 0;
    wcex.cbWndExtra     = 0;
    wcex.hInstance      = hInstance;
    wcex.hIcon          = LoadIcon(hInstance, MAKEINTRESOURCE(IDI_MY));
    wcex.hCursor        = LoadCursor(nullptr, IDC_ARROW);
    wcex.hbrBackground  = (HBRUSH)(COLOR_WINDOW+1);
    wcex.lpszMenuName   = MAKEINTRESOURCEW(IDC_MY);
    wcex.lpszClassName  = szWindowClass;
    wcex.hIconSm        = LoadIcon(wcex.hInstance, MAKEINTRESOURCE(IDI_SMALL));

    return RegisterClassExW(&wcex);
}

//
//   函数: InitInstance(HINSTANCE, int)
//
//   目标: 保存实例句柄并创建主窗口
//
//   注释:
//
//        在此函数中，我们在全局变量中保存实例句柄并
//        创建和显示主程序窗口。
//
BOOL InitInstance(HINSTANCE hInstance, int nCmdShow)
{
   hInst = hInstance; // 将实例句柄存储在全局变量中

   HWND hWnd = CreateWindowW(szWindowClass, szTitle, WS_OVERLAPPEDWINDOW,
      CW_USEDEFAULT, 0, CW_USEDEFAULT, 0, nullptr, nullptr, hInstance, nullptr);

   if (!hWnd)
   {
      return FALSE;
   }

   ShowWindow(hWnd, nCmdShow);
   UpdateWindow(hWnd);

   return TRUE;
}

//
//  函数: WndProc(HWND, UINT, WPARAM, LPARAM)
//
//  目标: 处理主窗口的消息。
//
//  WM_COMMAND  - 处理应用程序菜单
//  WM_PAINT    - 绘制主窗口
//  WM_DESTROY  - 发送退出消息并返回
//
//
LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
    switch (message)
    {
    case WM_COMMAND:
        {
            int wmId = LOWORD(wParam);
            // 分析菜单选择:
            switch (wmId)
            {
            case IDM_ABOUT:
                DialogBox(hInst, MAKEINTRESOURCE(IDD_ABOUTBOX), hWnd, About);
                break;
            case IDM_EXIT:
                DestroyWindow(hWnd);
                break;
            default:
                return DefWindowProc(hWnd, message, wParam, lParam);
            }
        }
        break;
    case WM_PAINT:
        {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hWnd, &ps);
            // TODO: 在此处添加使用 hdc 的任何绘图代码...
            EndPaint(hWnd, &ps);
        }
        break;
    case WM_DESTROY:
        PostQuitMessage(0);
        break;
    default:
        return DefWindowProc(hWnd, message, wParam, lParam);
    }
    return 0;
}

// “关于”框的消息处理程序。
INT_PTR CALLBACK About(HWND hDlg, UINT message, WPARAM wParam, LPARAM lParam)
{
    UNREFERENCED_PARAMETER(lParam);
    switch (message)
    {
    case WM_INITDIALOG:
        return (INT_PTR)TRUE;

    case WM_COMMAND:
        if (LOWORD(wParam) == IDOK || LOWORD(wParam) == IDCANCEL)
        {
            EndDialog(hDlg, LOWORD(wParam));
            return (INT_PTR)TRUE;
        }
        break;
    }
    return (INT_PTR)FALSE;
}
//五子棋胜利判定

// 检查水平方向是否有五子
int checkHorizontal(int board[20][20], int player) {
    for (int i = 0; i < 20; i++) {
        for (int j = 0; j < 16; j++) {
            if (board[i][j] == player && board[i][j + 1] == player && board[i][j + 2] == player &&
                board[i][j + 3] == player && board[i][j + 4] == player) {
                return 1;
            }
        }
    }
    return 0;
}

// 检查垂直方向
int checkVertical(int board[20][20], int player) {
    for (int i = 0; i < 16; i++) {
        for (int j = 0; j < 20; j++) {
            if (board[i][j] == player && board[i + 1][j] == player && board[i + 2][j] == player &&
                board[i + 3][j] == player && board[i + 4][j] == player) {
                return 1;
            }
        }
    }
    return 0;
}

// 检查对角线
int checkDiagonal1(int board[20][20], int player) {
    for (int i = 0; i < 16; i++) {
        for (int j = 0; j < 16; j++) {
            if (board[i][j] == player && board[i + 1][j + 1] == player && board[i + 2][j + 2] == player &&
                board[i + 3][j + 3] == player && board[i + 4][j + 4] == player) {
                return 1;
            }
        }
    }
    return 0;
}

// 检查反对角线
int checkDiagonal2(int board[20][20], int player) {
    for (int i = 0; i < 16; i++) {
        for (int j = 4; j < 20; j++) {
            if (board[i][j] == player && board[i + 1][j - 1] == player && board[i + 2][j - 2] == player &&
                board[i + 3][j - 3] == player && board[i + 4][j - 4] == player) {
                return 1;
            }
        }
    }
    return 0;
}

//每一回合查看全局
int checker(int board[20][20]) {
    if (checkHorizontal(board, 1) || checkVertical(board, 1) || checkDiagonal1(board, 1) || checkDiagonal2(board, 1)) {
        printf("白棋获胜\n");
    }
    else if (checkHorizontal(board, 2) || checkVertical(board, 2) || checkDiagonal1(board, 2) || checkDiagonal2(board, 2)) {
        printf("黑棋获胜\n");
    }
}

// 主函数，判断棋盘上是否有一方获胜并输出结果
int main() {
    int board[20][20] = { 0 }; // 初始化棋盘，所有位置为0，表示无棋子

    // 绘制主菜单
    //if click Start（#1名字、图标待商讨）
        //绘制棋盘，判断落子，记录click坐标x,y，得到i,j，改变board[][]
        //显示出所落棋子，%amount_of_players交替调用玩家棋子图片
        // 判定一方获胜后，显示（#1可插入胜利视频？设计玩家头像？）
        // 回到主菜单
    //if click Game Changer（#1）（#2模式待商讨）
        //绘制新界面，展示可选择的改变项目 
        //a、改变全局变量的值b、根据规则修改行动轮（#2可选择行动轮抽取能力卡？）c、（#1）（#2）
        // 回到主菜单
    //if click关于
        //显示制作人？（#1#2）
    //（#1#2）
        
 

    return 0;
}