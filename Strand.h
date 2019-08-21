#include <vector>
#include "llvm/ADT/Statistic.h"
#include "llvm/IR/Function.h"
#include "llvm/Pass.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/Value.h"
#include "llvm/IR/LLVMContext.h"

using namespace llvm;

typedef std::vector<llvm::Instruction *> strand;

void AddInst(strand* st, Instruction* Ins, strand* unuse);